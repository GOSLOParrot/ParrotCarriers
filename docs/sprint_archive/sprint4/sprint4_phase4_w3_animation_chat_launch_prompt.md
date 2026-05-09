---
status: ratified
category: chat-launch-prompt
status_note: "用于启动 ArSpike GOSLO 动画移植 chat（Minecraft Java Parrot 风格的 Idle/Fly/Dance/Sit）。建议模型：Sonnet 4.6 medium thinking。"
last_reviewed: 2026-04-30
---

# Launch Prompt — ArSpike GOSLO Animation Port (Minecraft Style)

> **复制下面 ```text``` 块的内容**到新 chat 即可。预设模型：**Sonnet 4.6 medium thinking**（备选 GPT-5.3 Codex high-fast；不要用 Opus 4.7 / Composer-2 / Gemini）。

```text
你是 ParrotCarriers Sprint4 Phase 4 ArSpike GOSLO 动画移植助手。
think in English，用中文回答。

## 第一步（不可跳过）

按顺序读以下 4 份文件，**全文**：

1. .cursor/memory/architecture/sprint4_phase4_w3_a2_a3_completion_20260430.md
   （上游 W3.A.2/A.3 完成报告 + 已有 producer events 接口契约）
2. .cursor/memory/parrot_behavior_rules.md §1 / §6（状态定义 + 动画清单）
3. unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/AnimationDriver.cs（当前
   程序化动画 baseline；你要扩展它，**不得破坏 wire mappers / producer
   events / 与 LifecycleHeartbeatPublisher 的契约**）
4. unity/ArSpike/Assets/Scripts/ParrotApp/Hands/PerchOnHand.cs（PerchedOnHand
   状态由它驱动，position 写入约定）

## 任务范围

把 GOSLO（unity/ArSpike/Assets/Models/GOSLO.glb，Blockbench 鹦鹉模型）
的程序化动画从当前简化版升级到 Minecraft Java Edition Parrot 风格：

- **Idle / Standing**：站立 + 头部慢速 cos 起伏 + 尾巴轻摆
- **Fly / Flying**：身体前倾 + 双翅高频拍动 + 尾巴平展
- **Dance / Party**：身体周期上下抖 + 头部快摇 + 双翅交替拍 + 尾巴扇形摇
- **Sit / Sitting**（可选 stretch）：腿弯曲 + 身体降低 + 翅膀贴身
- **PerchedOnHand**：保留 W3.A.2 行为（position 由 PerchOnHand 外部写，
  本类只做呼吸缩放 + head Tilt 摆动），**只补充翅膀 / 腿 / 尾巴的小幅
  idle 摆动**让站手上时不僵硬

## Minecraft 算法参考（公开 modding 教程惯用值；不 copy Mojang 代码）

参考来源（Yarn 1.20.3-pre1 javadoc + Forge javadoc + MCreator 教程）：

- 类：net.minecraft.client.model.ParrotModel
- 方法签名：setAngles(entity, limbAngle, limbDistance, age, headYaw,
  headPitch) —— age = ageInTicks，是连续浮点 tick 时钟（驱动 sin/cos）
- State enum：FLYING / STANDING / SITTING / PARTY / ON_SHOULDER
- 骨骼字段：body / tail / leftWing / rightWing / head / feather /
  leftLeg / rightLeg —— 与 GOSLO.glb 顶层 Empty 群组**1:1 对齐**
- 标准 coefficients（modding 教程 / Forge javadoc 公开；非 Mojang 私有
  代码，可作为起点然后真机/Editor 调优）：
  * Idle 头摇：cos(age * 0.7) * 0.4
  * 走路 limb swing：cos(limbSwing * 0.6662) * 1.4 * limbSwingAmount
  * 飞行翅膀（zRot）：cos(age * 0.6) * 0.5（带 +1.0 偏置保持张开）
  * 跳舞翅膀：高频高幅 ≈ cos(age * 0.3) * 0.4 + 头部抖
  * 尾摇：cos(age * 0.3) * 0.2
  * Party 头摇：sin(age * 0.6662) * 0.5（左右快摇）

**不要拍脑袋编系数**，每条公式都引用上面这一段，并在代码注释里标
"// modding standard, see Forge javadoc / Yarn 1.20.3"。

## 硬约束（绝不外溢）

1. **不动 W3.A.2/A.3 已建立的 wire 契约**：
   - `BodyState` enum 不删旧值，只可加 `Dance` / `Sit`（如果 enum 已有 5
     个状态以外的就不加）
   - `BodyStateToWire` / `HeadStateToWire` 静态 mapper 不动；新加 enum
     值要扩这两个方法 + 同步注释 lowercase / UPPERCASE 约定
   - `OnBodyStateWireChanged` / `OnHeadStateWireChanged` events 触发逻辑
     不变（SetState / SetHeadState 内 fire）
2. **不动 LifecycleHeartbeatPublisher / EcpStateDto**——动画扩展不应造成
   wire schema 变化
3. **不动 PerchOnHand 状态机**——它只是 Reflex 控制 position；本 chat
   只让 AnimationDriver 在 PerchedOnHand state 下补充 idle 翅膀腿尾摆动
4. **不发 LiveKit DataChannel**——动画是纯本地渲染层
5. **不实现 Animator / Animation Controller**——保持程序化（procedural）
   方案不变，所有动画通过 Update 里的 Transform.localRotation 驱动
6. **不引入新依赖包**（DOTween 等）

## GOSLO.glb 骨骼 Map（必须使用 case-insensitive FindDeep 匹配）

GLB 顶层 Empty 群组（旋转支点）：
- `head` —— 头部主旋转支点（包含 4 个 head mesh + feather 子群）
- `body` —— 身体主旋转支点
- `left_wing` → `left_wing_rotation` (子 Empty) —— **翅膀旋转用嵌套子 Empty**
- `right_wing` → `right_wing_rotation` (子 Empty)
- `left_leg` —— 腿旋转支点
- `right_leg`
- `tail` —— 尾巴旋转支点
- `feather` —— 头顶羽毛（在 `head` 群下面）

**当前 AnimationDriver.cs 只 cache 了 head + body**。本 chat 要扩
`Awake()` 里 FindDeep 把 `left_wing_rotation` / `right_wing_rotation` /
`left_leg` / `right_leg` / `tail` / `feather` 一并 cache 成 Transform 字段
（每个加 `_BaseRot` 缓存初始 quaternion，update 时 = base * delta）。

## Unity 坐标系映射（与 Mojang Mc Java 不同，必须翻译）

Mojang Java：左手系，xRot = pitch (X 轴俯仰), yRot = yaw (Y 轴左右),
            zRot = roll (Z 轴侧倾)，单位 radians
Unity      ：左手系 Y-up，Quaternion.Euler(pitch, yaw, roll) 单位 degrees

翻译规则：
- Mojang `xRot` (radians) → Unity `Quaternion.Euler(xRot * Mathf.Rad2Deg, 0, 0)`
- 翅膀 `zRot` 在 Mojang 是侧倾；Unity 里同样用 z 分量
- 翅膀左/右镜像：`right_wing` 的 zRot = -leftWing.zRot

`Mathf.Cos` / `Mathf.Sin` 已经是 Unity 内建，不需要 Mth.cos 等价物。

## 启动序

1. **第 1 步：读完上面 4 份文件 + 检查 GLB 实际节点名**
   （Console 里 `Debug.Log(transform name)` 或 ParrotSmokeScene 内
   Hierarchy 展开 ParrotModel 查看；以实际节点名为准，case-insensitive
   匹配）
2. **第 2 步：列改动清单**（类似 W3.A.2/A.3 chat 的 §A 决策锁风格），
   用户 sign off 后才动代码
3. **第 3 步：实现 + Editor smoke**
   - 改动文件预期：仅 `Parrot/AnimationDriver.cs`（+ 必要时
     `Parrot/ParrotController.cs` 的 `PlayAnimation` 字符串映射扩展）
   - 测试场景：复用 `Tools/Parrot/Build A2 Smoke Scene` 已生成的
     `ParrotSmokeScene.unity`
   - 加 Editor 入口（ContextMenu）：在 AnimationDriver 上加
     `[ContextMenu("Debug: Play Dance")]` / `Play Fly` / `Play Sit` 让
     用户能在 Inspector 一键切状态验收
4. **第 4 步：commit + 完成报告**
   - commit message 引用本 prompt + 上面 modding 参考
   - 完成报告写到
     `.cursor/memory/architecture/sprint4_phase4_w3_animation_completion_<date>.md`
     —— 与 W3.A.2/A.3 完成报告同结构

## 验收

Editor smoke：
1. ▶ Play → 默认 Idle 状态，鹦鹉站立 + 头慢摆 + 尾巴微摇 + 翅膀贴身呼吸
2. AnimationDriver 组件 ⋮ → `Debug: Play Fly`
   → 身体前倾 + 双翅高频对称拍动 + 尾巴平展
3. `Debug: Play Dance`
   → 身体上下抖 + 头部左右快摇 + 翅膀交替拍 + 尾巴扇形摇
4. `Debug: Play Sit`
   → 腿弯曲 + 身体降低 + 翅膀贴身
5. 触发 W3.A.2 的 `Debug: Fire 'index_finger_branch' gesture`（HandSource
   组件）→ PerchedOnHand state → 头依然 Tilt 摆动 + **翅膀 / 尾巴 / 腿**
   有轻微 idle 摆动（不僵硬，但不抢戏）
6. Console 期间持续输出 [Heartbeat:LOG] EcpState（A.3 心跳），且
   body_state wire 字段在每次 SetState 后立即变化

## 验收（不允许）

- 心跳 wire 字段命名变化（破坏 Brain ingest 准备）
- 翅膀 / 腿 / 尾巴 的 Transform 不通过 FindDeep 缓存，每帧 GetComponent
- 在 ParrotApp.Parrot 命名空间外加新文件
- 用 Coroutine 驱动动画（应该是 Update 里的 sin/cos 程序式）

## 联动状态（之前已落地，不要触碰）

Sprint4 Phase 4 W3 已完成的部分：
- W3.A.1 selection-C（Brain 端 cognitive tracker + state context + tool
  guards）—— 不动
- W3.A.2 perch_to_finger 全链路 —— 你扩 AnimationDriver 但不破坏其
  PerchedOnHand 行为
- W3.A.3 EcpState 三态事件驱动 + 1Hz 双触发 —— 你的 SetState /
  SetHeadState 调用会自动触发心跳事件，**不要自己直接发心跳**
- Brain 侧 W4-5 / W6-7 / GAP-1 EcpState ingest 在并行 chat 推进 —— 与本
  chat 完全正交

## Sprint4 终极目标（不要忘）

验证"协议升级后怎么提升 GOSLO 使用体感"。本 chat 的动画移植让 PerchedOnHand
"怎么了？" 表达更生动 + 让未来 Brain 端发 `animate("dance")` RPC 时有真
正的 Minecraft 风格 Dance 渲染，闭合"工具①体感闭环"的视觉那一半。
```

## 模型选择附注

- **Sonnet 4.6 medium thinking** = 首选，最稳遵守现有 wire 约束，移植
  代码 + 适配能力强
- GPT-5.3 Codex high-fast = 备选；更精简但偶有"擅自重构"风险
- 不要用：Opus 4.7（overkill，慢）/ Composer-2（不熟 ECP）/ Gemini-3.1
  （不熟 Unity）

## 启动后用户应做的事

1. 在新 chat 里粘贴上面 ```text``` 块全文
2. 等 AI 完成 §A 决策锁清单 → sign off → AI 写代码 → commit
3. 切回 Unity，Reimport 任何改动 + 在 ParrotSmokeScene 里跑 ContextMenu
   验收 4 个动画
4. 如果某个动画"看起来不像 Minecraft"，把 GIF / video 截给 AI，让它调
   coefficients；这是迭代过程，不是一次成型
