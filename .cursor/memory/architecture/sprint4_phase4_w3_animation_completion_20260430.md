---
status: ratified
category: completion-report
status_note: "Sprint4 Phase 4 W3 Animation-Port — Minecraft Java Parrot 风格 Idle/Fly/Dance/Sit 骨骼动画完成报告。"
last_reviewed: 2026-04-30
---

# Sprint4 Phase 4 W3 Animation-Port 完成报告（2026-04-30）

> **本文用途**：Minecraft Java Edition Parrot 风格程序化动画移植到 GOSLO.glb 的 authoritative 完成口径。
>
> **关联**：`sprint4_phase4_w3_animation_chat_launch_prompt.md`（任务定义）
> + `sprint4_phase4_w3_a2_a3_completion_20260430.md`（上游 wire 契约）

---

## §0 一句话总结

`AnimationDriver.cs` 完成从简化版到 **Minecraft Java Edition Parrot 风格**的程序化骨骼动画升级：6 个骨骼节点全部缓存、5 种状态完整动画化、wire 契约零改动、ContextMenu 验收入口已就位。

---

## §1 改动内容（单文件）

**改动文件**：`unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/AnimationDriver.cs`

### 1.1 BodyState enum 扩展

| 新增值 | wire 字符串 | 说明 |
|:--|:--|:--|
| `Dance` | `"dancing"` | 对应 parrot_behavior_rules §1.1 `DANCING` |
| `Sit` | `"idle"` | 视觉姿势变体，不新增 wire 状态（§6.1 `sit → IDLE`） |

旧值（`Idle / HeadBob / Fly / Perch / PerchedOnHand`）及其 wire mapping 全部保留不变。

### 1.2 新增骨骼缓存（Awake）

| 字段 | 节点名（case-insensitive FindDeep） | BaseRot |
|:--|:--|:--|
| `_leftWingRotTransform` | `left_wing_rotation` | ✅ |
| `_rightWingRotTransform` | `right_wing_rotation` | ✅ |
| `_leftLegTransform` | `left_leg` | ✅ |
| `_rightLegTransform` | `right_leg` | ✅ |
| `_tailTransform` | `tail` | ✅ |
| `_featherTransform` | `feather` | ✅（暂不 animate，缓存备用） |

节点未找到时 `Debug.LogWarning` 并跳过（不 throw）。

### 1.3 动画实现（Minecraft 算法参考：Forge javadoc / Yarn 1.20.3）

| 状态 | 新增动画层 | 核心公式（注释已标来源） |
|:--|:--|:--|
| **Idle** | 尾巴慢摆 + 翅膀轻呼吸 + 腿归位 | 尾：`cos(t·0.3·2π)·11°`；翅：`cos(t·0.8·2π)·8°`（zRot，左右镜像）|
| **HeadBob** | 所有新增骨骼 LerpToBase | 保持现有头部点头行为 |
| **Fly** | 双翅高频对称拍动 + 尾巴平展 + 腿归位 | 翅：`cos(t·0.6·2π)·29° + 57°` bias（Minecraft：0.5 rad + 1.0 rad）|
| **Dance** | 身体上下抖 + 头快摇 + 翅膀同步拍 + 尾巴扇摆 + 腿归位 | 头：`sin(t·0.6662·2π)·28°`；翅：`cos(t·0.3·2π)·23°`（0.4 rad ref）|
| **Sit** | 腿弯曲 + 身体下移 + 翅膀贴身 + 尾巴微抬 | 腿：30° pitch lerp；身体：-0.03m lerp |
| **Perch** | 所有新增骨骼 LerpToBase | 保持现有呼吸缩放 |
| **PerchedOnHand** | 翅膀/尾巴/腿轻微 idle 摆动（不抢戏） | 翅幅减半；尾幅减半；腿 ±4° 轮换 |

### 1.4 UpdateHeadOverlay 扩展

| 变化 | 细节 |
|:--|:--|
| Dance 状态跳过 | `if (CurrentState == BodyState.Dance) return;`（Dance 内部驱动头部） |
| Idle/Sit/Perch/HeadBob 时 HEAD_FORWARD 加 Minecraft 头摆 | `cos(t·0.7·2π)·14°` yaw（Minecraft 参考：0.7 Hz, 0.4 rad ≈ 23°，调小至 14° 更自然） |
| 其他状态 HEAD_FORWARD 保持归位 | 不变 |

### 1.5 ContextMenu 验收入口

```
Debug: Play Idle
Debug: Play Fly      （向 forward 方向飞 2m）
Debug: Play Dance
Debug: Play Sit
```

### 1.6 不变的契约（Zero-Drift 确认）

| 项目 | 状态 |
|:--|:--|
| `BodyState` 旧 5 个值 | 保留，未修改 |
| `BodyStateToWire` / `HeadStateToWire` 旧映射 | 保留，只追加 2 行 |
| `OnBodyStateWireChanged` / `OnHeadStateWireChanged` events | 不变 |
| `SetState` / `SetHeadState` 触发逻辑 | 不变 |
| `LifecycleHeartbeatPublisher` / `EcpStateDto` | 未触碰 |
| `PerchOnHand` 状态机 | 未触碰 |
| 无新依赖包 | ✅ |
| 无 Animator / Coroutine | ✅（全部 Update + Transform.localRotation） |

---

## §2 验收清单（Editor smoke）

在 `ParrotSmokeScene.unity` 中执行：

| # | 操作 | 预期 |
|:--|:--|:--|
| 1 | ▶ Play | 默认 Idle：鹦鹉站立 + 头慢速左右摆 + 尾巴轻摆 + 翅膀轻微呼吸缩放 |
| 2 | AnimationDriver ⋮ → `Debug: Play Fly` | 鹦鹉前移 + 双翅高频对称拍动（左右 zRot 镜像）+ 尾巴平展 |
| 3 | AnimationDriver ⋮ → `Debug: Play Dance` | 身体上下抖 + 头部快速左右摇 + 翅膀随节拍拍动 + 尾巴扇摆 |
| 4 | AnimationDriver ⋮ → `Debug: Play Sit` | 腿弯曲 + 身体微下沉 + 翅膀贴身（z-roll 内折）+ 尾巴微抬 |
| 5 | HandSource ⋮ → `Debug: Fire 'index_finger_branch' gesture` | PerchedOnHand：头 Tilt 摆动 + 翅膀/尾巴/腿有轻微 idle 摆动（不僵硬）|
| 6 | 全程 Console | 持续 `[Heartbeat:LOG]` body_state 在 SetState 后变化（A.3 事件驱动不变）|

**不允许出现**：
- 翅膀/腿/尾巴 frame-by-frame GetComponent（已全部 Awake 缓存）
- 心跳 wire 字段命名变化
- 新文件（本次改动仅 AnimationDriver.cs 一个文件）
- Coroutine 或新 MonoBehaviour

---

## §3 已知事项 / 调优建议

| 编号 | 事项 | 建议 |
|:--|:--|:--|
| A-1 | GLB 实际节点名需真机/Editor 验证 | 节点未找到时 Console 会打 `[AnimationDriver] Bone not found: 'xxx'`，按实际名调整 Inspector 字段即可（case-insensitive FindDeep）|
| A-2 | 翅膀 zRot 方向取决于 GLB 枢轴 | 若翅膀方向反了（扑地而非扑空），将 `flyWingOpenBias` 设为负值或在 Inspector 调 `flyWingFlapDegrees` 符号 |
| A-3 | Dance head yaw 与 HeadState 解耦 | Dance 进入后不强制 SetHeadState，离开后 UpdateHeadOverlay 自动恢复；不需要外部重置 |
| A-4 | `idleRotateSpeed` 默认 18°/s（持续旋转） | 若想要纯站立 Minecraft 风格可把 Inspector 改 0；现有行为已存在，本次未改 |
| A-5 | Minecraft 系数来自公开 modding 参考 | 所有 sin/cos 公式注释均标注 `// modding standard, see Forge javadoc / Yarn 1.20.3`；真机调优直接改 Inspector Serialized Fields |

---

## §4 后续入口

- **GAP-1 Brain EcpState ingest**：wire `"dancing"` 已就位，Brain ingest chat 只需扩 `ParrotBodyState` 加 `DANCING = "dancing"` 即可识别。
- **系数调优**：所有 Minecraft 系数暴露在 Inspector（Header 标注：`Idle Minecraft-style` / `Fly Minecraft-style` / `Dance Minecraft-style`），可在 Play 模式下实时拖动。
- **`Sit` 考虑单独 wire 值**：当前 Sit 走 `"idle"` wire，若 Brain 需要区分坐姿可单独加 `sitting` wire 值并扩 Brain enum（无破坏性变更）。

---

## §5 引用

- 任务定义：`sprint4_phase4_w3_animation_chat_launch_prompt.md`
- 上游 wire 契约：`sprint4_phase4_w3_a2_a3_completion_20260430.md`
- 行为规则：`parrot_behavior_rules.md` §1 / §2.2 / §6
- 算法来源：Forge javadoc / Yarn 1.20.3-pre1 / MCreator 教程（公开 modding 参考）
