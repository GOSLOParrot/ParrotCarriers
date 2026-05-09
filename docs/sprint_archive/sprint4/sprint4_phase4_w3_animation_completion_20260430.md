---
status: ratified
category: completion-report
last_reviewed: 2026-04-30
---

# W3 动画移植完成报告（2026-04-30）

## 完成内容

实现了 4 个基础程序化骨骼动画（`AnimationDriver.cs`）：

| 动画 | 描述 |
|------|------|
| **Fly** | `(1-cos)/2 * amp` 公式，翅膀从收拢到展开，无起跳无穿模；速度曲线：加速起步 + 近目标减速 |
| **Dance** | 整体弹跳 + body 左右摇 + 头反向摇 + 翅膀固定展开 |
| **PerchedOnHand** | 呼吸缩放 + 翅膀收拢 + 腿弯曲（抓树枝感） |
| **HEAD_TILT** | 歪头(0.4s) → 保持微摆(1.8s) → 恢复(0.4s) → 等待(0.5s) → 循环，不是左右摇头 |

附加：
- 翅膀轴测试 ContextMenu（Play 模式 → AnimationDriver 右键 → `Axis Test`）
- 坐标系映射分析文档（见 `animation_coord_system_analysis_20260430.md`）

---

## 发现的问题

### 1. 翅膀方向需实测确认
**现象**：默认轴 `NegZ` 实测导致翅膀向内合拢（穿进身体），已切换默认为 `PosZ` 修复。  
**根因**：gltfast X 轴取反后骨骼的本地轴方向无法纯粹推导，必须在 Unity 实测。  
**状态**：已提供 4 个轴测试入口，`PosZ` 当前实测方向正确。

### 2. 飞行动画公式错误
**现象**：`cos(t)` 从最大值起跳，且允许负值（翅膀低于收拢位），导致穿模 + 闪现。  
**修复**：改为 `(1 - cos(t)) / 2 * amp`，值域 `[0, amp]`，从 0 平滑起步。

### 3. 飞行为匀速平移
**现象**：`MoveTowards` 固定速度，无起步感，体感单调。  
**修复**：加入 `_flyCurrentSpeed` + `flyAcceleration` 加速度场 + 近目标平方根减速。

---

## Minecraft 风格动画未完成的原因

没有找到可验证的 vanilla `ParrotModel.java` 完整源码（SpigotMC 只有片段，javadoc 无实现）。  
用估算系数实现的结果与实际效果差距较大（party 翅膀逻辑完全不同、fly 偏置错误）。  

**后续**：获取 vanilla 源码（本地反编译 `client.jar`）后可对照实现 Minecraft 风格动画。  
现有 4 个基础动画作为占位，wire 契约完整、轴测试工具就位，随时可替换公式。

---

## 验收

`ParrotSmokeScene` Play 模式 → AnimationDriver 右键：
1. `Debug: Play Fly` — 鸟加速起飞，翅膀平滑从收拢到展开循环（2.5 Hz），5m 后降落
2. `Debug: Play Dance` — 身体弹跳 + 头部反向摆动 + 翅膀展开（不拍动）
3. 触发 perch gesture — 鸟站手指，翅膀收拢，腿弯曲，轻微呼吸
4. `Debug: Head Tilt` → 歪头 → 保持 → 自动恢复正头
