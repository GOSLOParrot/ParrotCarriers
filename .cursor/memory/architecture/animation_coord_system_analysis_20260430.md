---
status: ratified
category: technical-analysis
status_note: "Blockbench→glTF→gltfast→Unity 坐标系映射分析 + 翻译经验 + 遗留问题清单"
last_reviewed: 2026-04-30
---

# Blockbench→Unity 坐标系映射分析报告

> 作者：AI + 用户联合调试
> 场景：GOSLO.glb（Blockbench Minecraft-style 鹦鹉模型）→ gltfast v6 → Unity 2022.3 LTS
> 目的：解释 AnimationDriver 程序化动画的坐标翻译逻辑，记录已确认事项与未确认事项

---

## §1 坐标系链

```
Blockbench (右手 Y-up)
   → 导出 GLB/glTF (右手 Y-up，glTF 规范标准)
      → gltfast v4+ 导入 Unity (左手 Y-up，X 轴取反)
         → Unity 世界坐标 (左手 Y-up, Z-forward)
```

---

## §2 gltfast 的坐标转换规则（已确认）

**来源**：gltfast 官方升级文档 v4.x 章节（`com.unity.cloud.gltfast@6.2`）

> "the coordinate space conversion from glTF's right-handed to Unity's left-handed system is
>  performed by **inverting the X-axis** (before the Z-axis was inverted in v3 and earlier)"

### 轴映射

| glTF / Blockbench | Unity（gltfast v4+） |
|:---|:---|
| +X (模型右侧) | **-X** (取反) |
| +Y (上) | +Y (不变) |
| +Z (朝向观察者/模型正面) | +Z (不变) |

### 旋转换算

X 轴取反 → 坐标系从右手变左手：

| glTF 旋转方向 | Unity 中等价方向 |
|:---|:---|
| 绕 +X 旋转（pitch）| 与 Unity 本地 X 轴方向相同（净效果不变）|
| 绕 +Y 旋转（yaw） | 方向**反转** |
| 绕 +Z 旋转（roll）| 方向**反转**（CCW from +Z in glTF = CW from +Z in Unity）|

---

## §3 Blockbench 约定（已确认）

- Blockbench 使用**右手 Y-up** 坐标系
- glTF 规范规定："The front of a glTF asset faces +Z"
- Blockbench 导出时遵守此规范，模型正面对准 +Z
- gltfast v4+ 同样将 glTF +Z 与 Unity +Z 对齐（两者都是 forward）

---

## §4 GOSLO.glb 骨骼在 Unity 中的位置（推导）

从 Blockbench 截图（用户提供）：

| 骨骼 | Blockbench 位置 | → Unity 位置（X取反） |
|:---|:---|:---|
| `left_wing_rotation` | (-1.5, 4.6, -0.8) | (+1.5, 4.6, -0.8) |
| `left_wing` 组 | 负 X 侧（鹦鹉左边） | **正 X 侧**（Unity +X）|
| `right_wing` 组 | 正 X 侧（鹦鹉右边） | **负 X 侧**（Unity -X）|

⚠️ **关键结论**：Blockbench 里的"左翼"在 Unity 里位于 **+X** 方向，这与直觉相反（看名字以为在 -X）。

---

## §5 翅膀拍翅轴推导（理论）

**`left_wing` 组在 Unity +X 侧，翅膀末端在其下方（-Y 方向）。**

"翅膀向上拍"= 翼尖从 -Y 方向旋转至 +Y 方向：
- 绕 +Z 轴（左手规则）：+X 转向 +Y → 对于翼尖在 -Y 处，-Y 转向 +X（不是向上）
- 绕 **-Z 轴**（左手规则）：+X 转向 -Y → 翼尖从 -Y 转向 +X（也不对？）

等等——翅膀末端不完全在 -Y，而是在一定倾斜方向。具体结论取决于模型实际网格方向。

**理论最佳猜测**：`WingFlapAxisMode.NegZ`

**为什么**：vanilla Minecraft `leftWing.zRot = +value` 在 Minecraft（类 OpenGL 右手系）里让翼尖向上；
glTF +Z 旋转等价于 Unity **-Z** 旋转（见 §2 旋转换算）；因此对应到 Unity 的 `NegZ` 模式。

**⚠️ 未验证**：此推导仍有歧义，需在 Unity Play 模式用 ContextMenu `Debug: Axis Test *` 验证。

---

## §6 `left_wing_rotation` 的 Y=-180° 问题

从截图可见：`left_wing_rotation` 的旋转是 `(0, -180, 0)`。

**原因（推测）**：Blockbench 常用"Mirror"功能把右翼网格镜像复制到左侧，此时内部空体会带上 Y=-180° 旋转来保持网格朝向正确。

**后果**：
- 如果直接在 `left_wing_rotation` 上施加旋转，本地 Z 轴方向与 `right_wing_rotation` 相反
- 同样的 zRot 赋值会让两翅往相反方向运动

**代码解决方案**：
- `driveWingsFromShoulderGroup = true`（默认开启）
- 在父层 `left_wing` / `right_wing` 组施加旋转，绕过 Y=-180° 问题
- 代价：肩点 pivot 可能不在理想位置（取决于 Blockbench 中 `left_wing` 组的 pivot 位置）

---

## §7 程序化动画翻译经验总结

### 7.1 成功的部分

| 技术 | 结论 |
|:---|:---|
| FindDeep（case-insensitive）缓存骨骼 Transform | ✅ 工作正常，GLB 节点名完全匹配 |
| Quaternion.Euler + localRotation | ✅ 正确的施转方式 |
| PerchOnHand position 外部驱动 + AnimationDriver 只做骨骼动画 | ✅ 分层清晰 |
| Wire 契约（body_state / head_state 事件）| ✅ 未被破坏 |

### 7.2 踩坑记录

| 坑 | 原因 | 修复 |
|:---|:---|:---|
| 翅膀大幅向前伸 | 从 vanilla 抄的 +1.0 rad 偏置（57°）是错的，vanilla 零偏置 | 移除偏置，改为以中性位置为中心振荡 |
| Party 动作不像 Minecraft | 未找到 vanilla 实际源码，公式是估算 | 简化为：固定展翅 + 身体弹跳 |
| Idle 持续旋转 | 遗留了 `transform.Rotate(18°/s)` | 删除，改为轻微上下浮动 |
| 歪头变成了左右摇头 | `headTiltWiggleFrequency` 驱动的 sin 摆动 | 改为：歪过去→保持→恢复的相位循环 |
| 翅膀轴完全靠猜 | 没有在 Unity 里实测 | 加 4 个轴测试 ContextMenu，让用户实测确认 |

### 7.3 未解决问题

| # | 问题 | 待确认方式 |
|:---|:---|:---|
| A | 翅膀拍翅方向（NegZ / PosZ / X 轴？）| Unity Play 模式用 `Debug: Axis Test` |
| B | `left_wing` 组的 pivot 位置是否在肩点 | Hierarchy 选中 left_wing，查 Transform |
| C | Vanilla Minecraft Party/Fly 公式 | 自行 decompile client.jar，找 ParrotModel.java |
| D | 翅膀穿模（翅膀网格插入身体）| 取决于 pivot 位置，可能需回 Blockbench 调整 |

---

## §8 推荐下一步

### 短期（当前 sprint）
1. **Unity Play → 跑 4 个 Axis Test ContextMenu** → 确定 `wingFlapAxisMode`
2. 在 Hierarchy 查看 `left_wing` 的 pivot 位置是否在肩点
3. 根据实测调整 Inspector 参数（幅度、频率）

### 中期（获取 vanilla 数据后）
1. 用 Fernflower/Vineflower 反编译 Minecraft 1.20 `client.jar`
2. 找 `net/minecraft/client/model/ParrotModel.class`
3. 把 `setupAnim` 里每个骨骼赋值的完整公式抄出来
4. 用本报告 §2 的换算表，将 glTF/Minecraft 坐标转换为 Unity 坐标后重新实现

### 长期
- 若程序化动画持续不理想，考虑在 Blockbench 制作骨骼动画 clip，Unity Animator 驱动
- 优点：完全可控，无坐标系歧义；缺点：需要手工制作每个动作

---

## §9 引用来源

| 来源 | 内容 | 可信度 |
|:---|:---|:---|
| gltfast 官方文档 v4.x Upgrade Guide | X 轴取反规则 | ✅ 高（官方） |
| SpigotMC 论坛帖（2017）| vanilla PARTY 翅膀固定角度 ±0.349 rad | ✅ 中（贴出反编译代码）|
| 搜索 AI 汇总 | flying: cos * 0.25 rad 无偏置 | ⚠️ 中（未见原文验证）|
| Blockbench 截图（用户提供）| 骨骼层级 + pivot + rotation | ✅ 高（直接观察）|
| 理论推导（本报告 §5）| NegZ 轴推荐 | ⚠️ 低（待实测验证）|
