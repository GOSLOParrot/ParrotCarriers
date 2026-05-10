# Minecraft 鹦鹉动画移植笔记

更新时间：2026-05-10

## 结论

本项目对齐 **Minecraft Java Edition 1.20.1** 的鹦鹉模型动画。

正式 Unity 落点是：

- `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/AnimationDriver.cs`

旧的 `unity/ParrotDev` 只当历史/试验参考，不再作为这次动画实现入口。

## 不经过 Microsoft Store 的资料来源

Microsoft Store 或 Minecraft Launcher 登录失败时，不需要阻塞动画研究。Java 版版本信息可以从 Mojang 的 version manifest 找到：

- `https://piston-meta.mojang.com/mc/game/version_manifest_v2.json`

本次已缓存到本机、不要提交进 git：

- `D:\GOSLOParrot\minecraft_reference_cache\1.20.1\version.json`
- `D:\GOSLOParrot\minecraft_reference_cache\1.20.1\client.jar`
- `D:\GOSLOParrot\minecraft_reference_cache\1.20.1\client_mappings.txt`
- `D:\GOSLOParrot\minecraft_reference_cache\1.20.1\fcf_javap.txt`

1.20.1 对应的官方下载条目：

- client jar: `https://piston-data.mojang.com/v1/objects/0c3ec587af28e5a785c0b4a7b8a30f9a8f78f838/client.jar`
- client mappings: `https://piston-data.mojang.com/v1/objects/6c48521eed01fe2e8ecdadbd5ae348415f3c47da/client.txt`

`client.jar` 和映射文件只作为本地学习/核对资料使用，不把 Mojang 代码或 jar 放进仓库。

## 对照类

公开映射参考：

- Yarn 1.20.1 `ParrotEntityModel`: `https://maven.fabricmc.net/docs/yarn-1.20.1%2Bbuild.2/net/minecraft/client/render/entity/model/ParrotEntityModel.html`
- mappings.dev 1.20.1 `ParrotModel`: `https://mappings.dev/1.20.1/net/minecraft/client/model/ParrotModel.html`

本次用 `client_mappings.txt` 和 `javap` 确认：

- `net.minecraft.client.model.ParrotModel -> fcf`
- `net.minecraft.client.renderer.entity.ParrotRenderer -> fqk`
- `net.minecraft.world.entity.animal.Parrot -> bsb`

官方 pose 枚举：

- `FLYING`
- `STANDING`
- `SITTING`
- `PARTY`
- `ON_SHOULDER`

官方部件：

- `body`
- `tail`
- `leftWing`
- `rightWing`
- `head`
- `feather`
- `leftLeg`
- `rightLeg`

## Unity 状态映射

当前 `AnimationDriver` 保留项目原有 wire state，但默认走 Minecraft Java 1.20.1 pose 核心：

| 项目状态 | Minecraft pose | 备注 |
| --- | --- | --- |
| `Idle` / `Perch` | `STANDING` | 站立基础姿态 |
| `Walk` | `STANDING` | 使用官方腿部 `cos(limbSwing * 0.6662) * 1.4 * limbSwingAmount` |
| `Fly` | `FLYING` | 使用官方翅膀/尾巴/身体姿态与 ParrotRenderer 风格 flap progress |
| `Dance` | `PARTY` | 使用 tickCount 的 `cos/sin` 身体、头、翅、尾偏移 |
| `Sit` | `SITTING` | 使用官方 sit prepare 常量 |
| `PerchedOnHand` | `ON_SHOULDER` | 强制 animation progress = 0，避免手上停靠时乱拍翅 |
| `HeadBob` | `STANDING` + 项目头部 bob | 项目自定义状态，不是原版 pose |

## 实现注意

`AnimationDriver` 新增 `useMinecraftJavaParrotPose`，默认开启。

关键实现点：

- `prepareMobModel` 的 base pose 常量已搬到 Unity：羽冠、身体、翅膀、腿、坐下、飞行、跳舞腿部展开。
- `setupAnim` 的 pose 分支已按官方五态实现。
- `ParrotRenderer#getBob` 使用的 flap / flapSpeed / flapping 节奏在 Unity 中用 20 TPS 模拟。
- GOSLO.glb 的 `left_wing_rotation/right_wing_rotation` 已经烘焙镜像 yaw，所以默认不再把 Minecraft 的 `-PI` wing yaw 额外打到肩部组上；可用 `applyMinecraftWingYaw` 手动打开。
- Minecraft 模型 Y 轴是向下计数，Unity 本地 Y 向上，所以默认 `invertMinecraftYOffsets=true`。
- glTF 导入链路会镜像 X，所以默认 `invertMinecraftXOffsets=true`。

## Cursor 事实源

本次相关 Cursor 资料位置：

- 行为红线：`.cursor/memory/parrot_behavior_rules.md`
- 模块/接口骨架：`.cursor/memory/architecture/Interface/INDEX.md`
- 模块图快照：`.cursor/memory/architecture/module_map_p2.md`、`.cursor/memory/architecture/module_map_p4_snapshot.md`
- 错误复盘/护栏：`.cursor/memory/BigIssue.md`

后续如果继续改动画或协议，先读这些事实源，不要把 `docs/**` 当唯一真源。

