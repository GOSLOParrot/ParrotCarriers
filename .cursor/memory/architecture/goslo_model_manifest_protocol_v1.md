---
status: ratified-step1 / pending-unity-step2
category: protocol-spec
status_note: "GOSLO 模型 Manifest 协议 v1 — Step 1 (schema + meta plumbing + 文档) 落地，Step 2 (Unity ModelDriver / GosloLegacyController shim) 与 Step 3 (Brain animate model_id 参数) 待跟进。"
last_reviewed: 2026-05-06
authoritative_for: "ModelManifest schema 字段集 / Capability 注册规则 / Parrot Reflex 激活条件 / 坐标系单位约定 / 自定义模型作者接入步骤 / MMD→FBX→manifest 流程"
parent_doc: "../INDEX.md"
sources:
  - "goslo_model_modularization_launch_prompt_20260506.md (任务启动)"
  - "src/parrot/shared/model_manifest.py (代码 SSOT)"
  - "src/parrot/shared/parrot_actions.py (ParrotAnimation 8 项 wire 锁)"
  - "src/parrot/shared/ecp.py (EcpCommand.meta wire-不动 槽位)"
  - "sprint4_phase4_entry_20260430.md §8 (Phase 4 决策锁)"
related:
  - "lineb_implementation_completion_20260504.md (完成报告样板)"
  - "ar_workspace_index.md (AR 工作区聚合)"
---

# GOSLO 模型 Manifest 协议 v1

> **本文用途**：自定义模型作者（人 / AI CLI）把任意 Unity 模型接入 ParrotCarriers 协议层的 SSOT 文档。读完本文 + 写一份 manifest.json + 写一个 IParrotController 实现，就能在 Unity 端用 Brain 的既有 RPC 接口控制模型。
>
> **范围**：协议层（Pydantic schema + 接入约定 + 坐标系/缩放规则 + Reflex 激活条件 + 端到端 walkthrough）。**不包括** Unity 端 ModelDriver / GosloLegacyController 实现细节（Step 2 落地后回填）、AI CLI 实现（Step 4 落地后回填）。
>
> **基调**：协议哲学是"动作完全开放注册 + ParrotAnimation enum 8 项是 Brain 词汇表 + Reflex 触发条件"（设计 chat 2026-05-06 Q-A sign off）。模型作者声明能力，Brain 调用能力，Unity 端按 capability_id 路由到控制器内部 handler。

---

## §0 TL;DR

| 维度 | 答案 |
|:--|:--|
| 协议核心 | `ModelManifest` Pydantic schema（`src/parrot/shared/model_manifest.py`）|
| 模型作者要写什么 | 1 份 `manifest.json` + 1 个实现 `IParrotController` 的 MonoBehaviour |
| Brain LLM 词汇表 | `ParrotAnimation` enum 8 项（wire-locked，**永不增删**）|
| 自定义动作 | 自由命名 `capability_id`（不在 8 项内的 Brain LLM 不主动调用，可走 dispatch_task / 后续工具触发）|
| Parrot Reflex 层 | 任意 capability_id ∈ ParrotAnimation 8 项 → Reflex 激活（呼吸 / idle 摇头 / tail sway）；否则关闭 |
| 多 model 路由 | wire 走 `EcpCommand.meta["model_id"]`（0 wire 改动）；Unity 端 `ParrotRegistry`（P1 单 active stub / P3 多 actor 真路由）|
| 坐标系锁 | `+Z` forward / `+Y` up / 1 unit = 1 米 / 桌宠基线 0.20m（minimal_lock）|
| 兼容性 | 旧 `AnimationDriver.cs` Step 2 改成 deprecated shim，转发 `GosloLegacyController`；GOSLO 行为 0 漂移 |

---

## §1 文件路由

| 要找什么 | 去哪里 |
|:--|:--|
| 任务启动 prompt | `goslo_model_modularization_launch_prompt_20260506.md` |
| 协议代码（Pydantic SSOT） | `src/parrot/shared/model_manifest.py` |
| 协议测试 | `tests/test_shared/test_model_manifest.py` |
| wire 路由槽位 | `src/parrot/shared/ecp.py` (`EcpCommand.meta`) + `wrap_legacy_rpc_payload(meta=...)` |
| Brain LLM 词汇表 | `src/parrot/shared/parrot_actions.py` (`ParrotAnimation` enum) |
| Phase 4 §8 决策锁 | `architecture/sprint4_phase4_entry_20260430.md §8` |
| **暗线审计 / 残余债清单 / p2.5 p3 前瞻需求注记** | `goslo_modularization_residual_debt_20260506.md` |
| **Step 5 完成报告** | `goslo_modularization_completion_20260506.md` |
| **AI CLI** | `src/scripts/asset_to_manifest.py` |
| Unity ModelDriver / GosloLegacyController | `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/` (Step 2 后回填) |
| 默认 GOSLO manifest | `unity/ArSpike/Assets/Resources/parrot_models/goslo_default.json` (Step 2 后回填) |
| AI CLI | `src/scripts/asset_to_manifest.py` (Step 4 后回填) |

---

## §2 协议哲学（设计 chat 2026-05-06 Q-A sign off）

### §2.1 双层架构 — 显式能力层 + Reflex 层

```
Brain LLM
  │
  ├── 显式调用（词汇表 = ParrotAnimation enum 8 项）
  │     └── animate(animation_name="fly", model_id="...")
  │            ↓
  │            EcpCommand.meta["model_id"] → Unity ParrotRegistry → IParrotController.ApplyCapability("fly", ...)
  │                                                                         ↓
  │                                                                    控制器内部 handler（Animator state / clip / 自定义代码）
  │
  └── 自定义调用（dispatch_task / 后续 tool 扩展）
         └── capability_id="dance_q_pose"（Brain LLM 不知道，但可被对话触发）
                ↓
                同样路径
                
Unity ModelDriver
  │
  ├── 加载 ModelManifest.json
  ├── 反射实例化 controller_type
  ├── 自动按 default_pet_height_m 缩放（auto_scale_to_pet_height=True 时）
  ├── 注册到 ParrotRegistry（model_id → controller）
  └── 若 manifest.parrot_reflex_enabled → 附挂 ReflexLayer MonoBehaviour
                                              ↓
                                              次级程序化行为（呼吸 / idle 摇头 / tail sway）
```

### §2.2 ParrotAnimation enum 8 项的双重身份

不是 "模型必须实现的清单"。是：

1. **Brain LLM 词汇表** — Gemini 学会调用这 8 个 capability_id（`idle / fly / dance / wing_flap / perch / sit / head_bob / sleep`），不会自己发明新的。
2. **Parrot Reflex 触发器** — 模型若声明实现这 8 项中的**任意一项**，Unity ModelDriver 会自动给它附加"鸟特有的次级小动作"（呼吸 / idle 摇头 / tail sway）。

**模型作者的选择**：
- 想做"鹦鹉系"模型：声明几项或全部 ParrotAnimation enum capability_id → Brain 可控 + 自动 Reflex
- 想做"非鸟系"伴侣（人形 / Q 版 / 机器人）：完全不声明 reserved id，自定义所有 capability_id → Brain 不主动调用（除非通过 dispatch_task）+ 无 Reflex
- 混合：声明部分 reserved id（如只 `idle` / `head_bob`）+ 自定义（如 `wave_hand`）→ Brain 知道前者 + Reflex 启用 + 后者由 dispatch 触发

### §2.3 wire 不动的设计

`EcpCommand` 已有 `meta: dict[str, Any]` 字段（Phase 4 §8 锁住的 wire schema 内本来就有的）。`model_id` 走 `meta["model_id"]`：

```python
# Brain side
payload, _command = wrap_legacy_rpc_payload(
    {"animation": "fly"},
    kind=EcpCommandKind.ANIMATE,
    target={...},
    actor="brain.tools.animate",
    meta={"model_id": "owl_v1"},  # 路由提示
)
```

**0 wire schema 变化** + **0 cs_parity 影响**（cs_parity 守的是 `EcpEventTypeNames`，不是 EcpCommand 字段集） + **0 ADR 需要**。

Unity 侧的 `EcpCommandDto` C# struct 当前**没有** `meta` 字段，但 `JsonUtility` 反序列化时会**忽略未识别字段**（这是 wire-不动设计的安全网）。Step 2 Unity 端要读 `meta["model_id"]` 时再决定是给 `EcpCommandDto` 加 `meta` typed 字段，还是把 `model_id` 提到 RPC payload 顶层（`FlyToPayload` / `AnimatePayload` 加 `string model_id`）— 这是 Step 2 设计窗口。

---

## §3 ModelManifest schema 字段表（v1）

完整定义见 `src/parrot/shared/model_manifest.py`。本节按字段说明**意图**与**约束**。

### §3.1 顶层字段

| 字段 | 类型 | 默认 | 说明 |
|:--|:--|:--|:--|
| `schema_version` | `int` | `1` | manifest schema 版本号；字段集变动时升 |
| `manifest_version` | `int` | `1` | 单个 manifest 文件版本（同一 model_id 不同版本迭代） |
| `model_id` | `str` (1-64) | 必填 | 全场景唯一 ID（如 `"GOSLO_default"` / `"owl_v1"` / `"qfufu_v1"`），不允许含空白 / 路径分隔符 |
| `display_name` | `str` | `""` | UI 显示名（中文 OK） |
| `asset_path` | `str` (1-256) | 必填 | Unity Resources 路径（如 `"parrot_models/owl_v1"`），不含扩展名 |
| `controller_type` | `str` (1-256) | 必填 | MonoBehaviour 全限定类名（如 `"ParrotApp.Parrot.OwlController"`），ModelDriver 反射实例化 |

### §3.2 坐标系 / 单位 / 缩放（minimal_lock）

| 字段 | 类型 | 默认 | 说明 |
|:--|:--|:--|:--|
| `forward_axis` | `"+X"/"-X"/"+Y"/"-Y"/"+Z"/"-Z"` | `"+Z"` | 模型正面朝向轴（与 glTF / Unity 默认对齐）|
| `up_axis` | 同上枚举 | `"+Y"` | 模型上方向轴 |
| `unit_meters` | `float > 0` | `1.0` | 1 Unity unit = N 米；MMD 模型常见 `0.08`（1 unit ≈ 8cm，需缩放） |
| `default_pet_height_m` | `float > 0` | `0.20` | 桌宠基线高度（米）；ModelDriver 启动按比例自动缩放 |
| `auto_scale_to_pet_height` | `bool` | `true` | 是否启用自动缩放；GOSLO_default 应填 `false`（保持现有大小）|

**为什么是 minimal_lock 而非 strict_lock**（设计 chat Q-D）：模型差异大，过严会让大量正常模型不能接入；只锁"必须告诉协议层的"东西，骨骼名 / handler 命名 / 动画曲线全交给作者。

### §3.3 capabilities — 能力声明列表

```python
class Capability(BaseModel):
    capability_id: str            # 自由命名；落入 RESERVED_PARROT_CAPABILITY_IDS 触发 Reflex
    kind: CapabilityKind          # POSE / ANIMATION / PROCEDURAL
    handler: str = ""             # 控制器内部 method / Animator state / clip 名（Unity 端自由）
    parameters: dict[str, Any] = {}
    description: str = ""
```

**`kind` 的语义**（informational，Unity 路由不依赖它）：
- `POSE` — 持续状态（`fly` / `perching` / `dancing`），下一次切换前一直保持
- `ANIMATION` — 一次性动作（`wing_flap` / `head_bob`），完成后回到上一个 pose
- `PROCEDURAL` — 控制器自定义代码路径（混合 pose + 微调 / IK）

`capability_id` 在 manifest 内必须**唯一**（重复会 schema 校验失败）。

### §3.4 capability_id 命名约定（推荐，非强制）

| 命名空间 | 示例 | 谁能调用 |
|:--|:--|:--|
| Reserved（Brain 词汇表） | `idle` / `fly` / `dance` / `wing_flap` / `perch` / `sit` / `head_bob` / `sleep` | Brain LLM 通过 `animate` tool 主动调用 + Reflex 自动激活 |
| 自定义动作 | `dance_q_pose` / `wave_hand` / `bow` / `combat_idle` | 仅显式 dispatch_task / 后续工具扩展触发 |

Reserved 集合 = `frozenset(a.value for a in ParrotAnimation)`，定义在 `model_manifest.py`，与 wire 锁绑定。

### §3.5 元数据

| 字段 | 类型 | 说明 |
|:--|:--|:--|
| `preview_image` | `str` | UI / 资产浏览器预览图（Resources 路径） |
| `author_meta` | `dict[str, str]` | 自由元数据（作者 / 来源 / 许可证 / MMD 原作者 / 等） |

### §3.6 派生属性（不可直接赋值，只读）

| 属性 | 计算方式 | 用途 |
|:--|:--|:--|
| `parrot_reflex_enabled` | 任意 `capability.is_reserved_parrot_id == True` | Unity ModelDriver 决定是否附挂 ReflexLayer |
| `declared_capability_ids` | `frozenset(c.capability_id for c in capabilities)` | Brain `query_scene` 暴露给 LLM；Unity 端 graceful-ignore 未声明的调用 |
| `supports(capability_id)` | `capability_id in declared_capability_ids` | 调用前快路径检查 |

---

## §4 自定义模型接入步骤（人手版）

### §4.1 Step 1 — 准备 Unity 资产

把模型 prefab 放到 `unity/ArSpike/Assets/Resources/parrot_models/<model_id>.prefab`：
- 若来源是 `.fbx`：先 Drag-In Unity，调好材质，做成 Prefab
- 若来源是 `.glb`：先用 [glTFast](https://github.com/atteneder/glTFast) 导入
- 若来源是 MMD `.pmx + .vmd`：见 §5 walkthrough

prefab 必须能在场景里正常显示（不依赖编辑器 Prefab Variant）。

### §4.2 Step 2 — 写 IParrotController 实现

新建 `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/<ModelName>Controller.cs`：

```csharp
using ParrotApp.Parrot;  // IParrotController 接口（Step 2 落地后填详情）
using UnityEngine;

namespace ParrotApp.Parrot
{
    public class OwlController : MonoBehaviour, IParrotController
    {
        public string ModelId => "owl_v1";
        public IReadOnlyCollection<string> SupportedCapabilities => _caps;
        public bool ParrotReflexEnabled => true;  // 由 ModelDriver 注入，本地缓存

        private static readonly HashSet<string> _caps = new() { "idle", "fly", "head_bob" };

        public bool ApplyCapability(string capabilityId, string parametersJson)
        {
            switch (capabilityId)
            {
                case "fly":     return DoFly(parametersJson);
                case "idle":    return DoIdle();
                case "head_bob":return DoHeadBob();
                default:        return false;  // graceful-ignore unsupported
            }
        }

        private bool DoFly(string paramsJson) { /* ... */ return true; }
        // ...
    }
}
```

**实现要点**：
- 未声明的 capability_id 必须返回 `false`（让上层 RPC 把 ack 改成 `failed/capability_unsupported`，不要默默吃掉）
- 返回 `true` = 已开始执行（不一定完成；EcpAck 的 completion 状态由现有 `ParrotRpcHandler` 管）
- `parametersJson` 是 RPC payload 的 `parameters` 字段（如 `flyTo` 的 `{"x":...,"y":...,"z":...}` 部分），自由解析

### §4.3 Step 3 — 写 manifest.json

新建 `unity/ArSpike/Assets/Resources/parrot_models/<model_id>.json`：

```json
{
  "schema_version": 1,
  "manifest_version": 1,
  "model_id": "owl_v1",
  "display_name": "Sparkle the Owl",
  "asset_path": "parrot_models/owl_v1",
  "controller_type": "ParrotApp.Parrot.OwlController",
  "forward_axis": "+Z",
  "up_axis": "+Y",
  "unit_meters": 1.0,
  "default_pet_height_m": 0.20,
  "auto_scale_to_pet_height": true,
  "capabilities": [
    {"capability_id": "idle",     "kind": "pose", "handler": "Idle"},
    {"capability_id": "fly",      "kind": "pose", "handler": "Fly"},
    {"capability_id": "head_bob", "kind": "pose", "handler": "HeadBob"}
  ],
  "preview_image": "parrot_models/owl_v1_preview",
  "author_meta": {
    "author": "ExampleAuthor",
    "source_format": "FBX",
    "license": "CC-BY-4.0"
  }
}
```

### §4.4 Step 4 — 验证（Python 侧）

```bash
python -c "
from pathlib import Path
import json
from parrot.shared.model_manifest import ModelManifest
raw = json.loads(Path('unity/ArSpike/Assets/Resources/parrot_models/owl_v1.json').read_text(encoding='utf-8'))
m = ModelManifest.model_validate(raw)
print('OK', m.model_id, 'reflex=', m.parrot_reflex_enabled, 'caps=', m.declared_capability_ids)
"
```

输出预期：`OK owl_v1 reflex= True caps= frozenset({'idle', 'fly', 'head_bob'})`

### §4.5 Step 5 — Unity 端联调

Step 2 落地后回填具体场景挂载步骤（ModelDriver / ParrotRegistry GameObject 配置 / 切换 model_id 测试）。

---

## §5 MMD `.pmx` + `.vmd` → FBX → manifest 端到端 walkthrough（设计 chat Q5 目标）

> 这是 user 在设计 chat 给的具体目标场景：找二头身 Q 版大头橘福福（MMD `.pmx` 模型），拿到动作文件 `.vmd`，转成 Unity 可用的带动画 FBX，接入本协议。

### §5.1 .pmx + .vmd → FBX

推荐工具链（开源，Sprint4 当前未集成 — 留给模型作者侧）：

1. **MMD2FBX**（社区活跃维护的 MMD → FBX 转换器，参考实现：[mmd2fbx](https://github.com/uuz/mmd2fbx) 或 Blender MMD Tools 插件 + FBX 导出）
2. **Blender MMD Tools**：
   - 安装 [mmd_tools](https://github.com/UuuNyaa/blender_mmd_tools) Blender 插件
   - 导入 `.pmx` → 加载 `.vmd` → 烘焙到骨骼动画 → FBX 导出
   - 导出时勾选 Apply Transform / Add Leaf Bones=False / Animation=Baked
3. 导出的 FBX **直接拖入** `unity/ArSpike/Assets/Resources/parrot_models/<model_id>/`

### §5.2 Unity 侧准备

1. 选中导入的 FBX → Rig 设为 **Generic** 或 **Humanoid**（Q 版人形通常 Humanoid 更合适）
2. Animation 标签页：检查 AnimationClip 列表，重命名为有意义的名字（`Idle.anim` / `Wave.anim` / `Dance.anim`）
3. 拖到场景：调整 Transform 看大小是否合理（MMD 单位通常 ≠ Unity 单位）
4. 制作成 Prefab，放到 Resources 下

### §5.3 写 manifest

MMD 模型的关键差异点：
- **`unit_meters`**：MMD 默认 1 unit ≈ 8cm，所以 `unit_meters = 0.08`
- **`auto_scale_to_pet_height = true`**：让 ModelDriver 按 `default_pet_height_m` 自动缩到桌宠尺寸
- **大概率不在 ParrotAnimation 8 项里**：MMD 动作通常是舞蹈 / 表情 / 摆 pose，自由命名 `capability_id`

示例 `qfufu_v1.json`：

```json
{
  "schema_version": 1,
  "manifest_version": 1,
  "model_id": "qfufu_v1",
  "display_name": "橘福福",
  "asset_path": "parrot_models/qfufu_v1",
  "controller_type": "ParrotApp.Parrot.QFufuController",
  "forward_axis": "+Z",
  "up_axis": "+Y",
  "unit_meters": 0.08,
  "default_pet_height_m": 0.18,
  "auto_scale_to_pet_height": true,
  "capabilities": [
    {"capability_id": "idle",         "kind": "pose",       "handler": "Idle"},
    {"capability_id": "wave_hand",    "kind": "animation",  "handler": "Wave"},
    {"capability_id": "dance_q_pose", "kind": "animation",  "handler": "Dance"},
    {"capability_id": "bow",          "kind": "animation",  "handler": "Bow"}
  ],
  "author_meta": {
    "source_format": "MMD .pmx + .vmd via Blender mmd_tools",
    "mmd_author": "<MMD 模型作者>",
    "license": "<原 MMD 许可证 — 转换前必读>"
  }
}
```

注意 `idle` 在 reserved 集合内 → `parrot_reflex_enabled = True`（即使其他都是自定义动作，只要有一项触发了，Reflex 层就开）。如果你想让这个 Q 版完全不带"鸟性"（idle 不要呼吸 / 摇头），就把 `idle` 也改成自定义名（如 `qfufu_idle`），Reflex 关闭。

### §5.4 写 QFufuController.cs

```csharp
using ParrotApp.Parrot;
using UnityEngine;

namespace ParrotApp.Parrot
{
    public class QFufuController : MonoBehaviour, IParrotController
    {
        public string ModelId => "qfufu_v1";
        public IReadOnlyCollection<string> SupportedCapabilities => _caps;
        public bool ParrotReflexEnabled { get; set; }  // ModelDriver 注入

        private static readonly HashSet<string> _caps = new() {
            "idle", "wave_hand", "dance_q_pose", "bow"
        };

        private Animator _animator;

        void Awake() { _animator = GetComponent<Animator>(); }

        public bool ApplyCapability(string capabilityId, string parametersJson)
        {
            // capability_id → Animator state name 直接映射（最简方案）
            switch (capabilityId)
            {
                case "idle":         _animator.Play("Idle"); return true;
                case "wave_hand":    _animator.Play("Wave"); return true;
                case "dance_q_pose": _animator.Play("Dance"); return true;
                case "bow":          _animator.Play("Bow"); return true;
                default: return false;
            }
        }
    }
}
```

### §5.5 Brain 侧调用

Brain LLM 默认只会调 `animate(animation_name="idle")` — 因为它只学过 ParrotAnimation enum 8 项。其他自定义动作（`wave_hand` / `dance_q_pose` / `bow`）目前需要：

- 通过 `dispatch_task` tool 间接（需扩展 dispatch_task 能下发 capability 调用 — 后续 chat）
- 或人工通过 Unity 端 ContextMenu / Editor 工具触发（开发期）
- 或后续新增 `play_capability(model_id, capability_id, params)` tool（设计 chat 后 P3+）

---

## §6 硬约束 — **永不触动**

| 锁 | 不能动什么 | 来源 |
|:--|:--|:--|
| Phase 4 §8 L1-L13 wire schema | `EcpEvent` / `EcpState` / `EcpAck` / `EcpCommand` 顶层字段集 | `sprint4_phase4_entry_20260430.md §8.1` |
| `ParrotAnimation` enum | 8 项不增不减；自定义走 `capability_id` 自由命名 | `parrot_actions.py` |
| `ParrotBodyState` enum | 5 项 wire 锁 | 同上 |
| `BehaviorMode` Flag enum | 5 项 wire 锁 | 同上 |
| `EcpEventTypeNames` cs_parity | 4/4 测试不破 | `tests/test_ecp_event/test_cs_parity.py` |
| `EcpCommand.meta` 字段类型 | 仍是 `dict[str, Any]`，不窄化 | `ecp.py` |

**自定义动作绕开 enum 锁的合法路径**：
- 模型 manifest 声明自定义 `capability_id`（如 `dance_q_pose`）
- IParrotController 实现路由该 capability_id
- 通过 `dispatch_task` / 后续 tool 触发（不通过 `animate` enum 校验）

不允许：
- 在 `ParrotAnimation` enum 加 `DANCE_Q_POSE` 项
- 在 `EcpCommand` 加 `model_id: str = ""` 顶层字段（用 `meta` 即可）
- 在 `EcpCommandDto` C# 里加跨 wire 的新字段（除非走完 cs_parity 升级流程）

---

## §7 已知留白（Step 2-5 待回填）

| 项 | 状态 | 落点 |
|:--|:--|:--|
| Unity `IParrotController` 接口完整签名 | Step 2 | `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/IParrotController.cs` |
| Unity `ModelDriver` 实现 + Resources 加载约定 | Step 2 | 同目录 `ModelDriver.cs` |
| `ParrotRegistry` P1 单 active stub | Step 2 | 同目录 `ParrotRegistry.cs` |
| `GosloLegacyController` shim（包装现有 AnimationDriver 行为） | Step 2 | 同目录 `GosloLegacyController.cs` |
| `Resources/parrot_models/goslo_default.json`（兼容性基线） | Step 2 | `unity/ArSpike/Assets/Resources/parrot_models/` |
| `EcpCommandDto` 是否加 `meta` 字段 / 还是 RPC payload 加 `model_id` 顶层字段 | Step 2 决策 | `EcpDtos.cs` 或 `FlyToPayload` / `AnimatePayload` |
| Brain `animate.py` 加 `model_id` 参数 | Step 3 | `src/parrot/brain/tools/animate.py` |
| AI CLI `asset_to_manifest.py` MVP | Step 4 | `src/scripts/asset_to_manifest.py` |
| MMD demo 端到端样例资产 | Step 4 | user 提供 |
| 完成报告 | Step 5 | `architecture/goslo_model_modularization_completion_<date>.md` |

---

## §8 变更日志

- **2026-05-06 (Step 1)**：本文创建。落地 `parrot.shared.model_manifest` Pydantic schema + `wrap_legacy_rpc_payload` `meta` kwarg + 协议规则文档 v1。Step 1 验收：
  - `tests/test_shared/test_model_manifest.py` 全绿
  - `tests/test_scheduler/test_ecp.py` 新增 2 个 meta kwarg 用例全绿
  - 既有 `tests/test_ecp_event/test_cs_parity.py` 4/4 不破
  - Phase 4 §8 wire schema 0 漂移
