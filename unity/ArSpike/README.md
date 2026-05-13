# ArSpike

## Current App Directory Rule (2026-05-13)

The formal Unity App center is `Assets/ParrotApp/**`.

- Runtime scripts: `Assets/ParrotApp/Runtime/Scripts/**`
- Startup scene: `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity`
- Runtime resources: `Assets/ParrotApp/Resources/**`
- Curated App art: `Assets/ParrotApp/Art/AppV1/**`
- Models: `Assets/ParrotApp/Models/**`
- Test evidence only: `Assets/Tests/Smoke/**` and `Assets/Tests/NerTuning/**`

The old duplicate script root `Assets/Scripts/ParrotApp/**` has been removed
and must not be recreated. Read
`codex_workspace/design_workspace/backend_interface_map/app/unity_project_inventory_app_ssot_20260513.md`
before changing Unity directories, scenes, resources, models, art, or Build
Settings.

Unity **2022.3 LTS** 下的工程仓位。当前承担两个角色（2026-04-29 起）：

1. **AR 基线探针**（原始角色）：AR Mobile Template + AR Foundation 5.2.2，用于平面检测 / 放置等 AR 基线验证，是 `.cursor/skills/ar-foundation-api` 与 `ar-foundation-samples` 的对照实现。
2. **正式 AR App 接口工作区**（Sprint4 起新增）：GOSLOParrot 正式 App 的 C# 接口与脚本骨架在此搭建；**不含美术资产**（白模 / 接口工作区）。带资产的打包结果未来落到 `unity/GOSLOParrot/`（暂未创建）。

`unity/ParrotDev` 是 Sprint 1–3 测试床；Sprint4 起冻结，仅作为 Sprint3 真机调试的留档与回归对照。新代码不再进 ParrotDev。

## Sprint4 进行中的迁移

ECP 协议代码与正式 App 脚本骨架的逐步迁移记录在：

- `codex_workspace/design_workspace/archive/unity_parrotapp_scripts_migration_20260429.md` — 当前迁移状态、依赖搬迁顺序、不搬迁清单、不允许误读。

修改 ECP 行为只动 ArSpike 这一份；ParrotDev 那份不再同步。

## AR Foundation 版本说明

- **模板默认**：通过 Unity Hub 创建该工程时，Package Manager 会为 AR Foundation / ARCore / ARKit 解析到 **5.2.x**。
- **本仓库改动**（与 ParrotCarriers 对齐）：三个包已**显式锁为 5.2.2**，与 `unity/ParrotDev`、`.cursor/rules/ar-foundation.mdc` 及 `.cursor/skills/ar-foundation-api` 的当前 notice 一致。5.2.2 仍是 Unity 2022.3 LTS 兼容线，不等于 Unity 6 / AR Foundation 6.x。
  - `com.unity.xr.arfoundation` → `5.2.2`
  - `com.unity.xr.arcore` → `5.2.2`
  - `com.unity.xr.arkit` → `5.2.2`
- **升级原因**：ARCore XR Plugin 5.2.2 解决 Android 15+ / Google Play 16KB native page alignment 相关问题；本仓库用到的 AR Foundation API 面在 5.1 → 5.2 中保持兼容。

直接依赖写在 `Packages/manifest.json`；`Packages/packages-lock.json` 已同步上述版本，避免仅改 manifest 时锁文件仍指向旧版。

## XR Plugin Management（`com.unity.xr.management`）

- **不要在 manifest 里显式钉死**该包，除非你有明确理由。AR Foundation 5.2.x 在包元数据里对 `xr.management` 的要求是下界（锁文件里常写成 `4.0.1`）；Unity UPM 会在**单一版本**上收敛，钉死顶层版本与主工程“不钉、解析为 4.4.0”容易造成团队间解析结果不一致，偶发 Package Manager 警告或与编辑器补丁行为差异。
- **官方层面**：未见到「必须 4.5.0 才能打 AR 包」的硬性要求；依赖冲突通常表现为 UPM 明确报错（无法满足版本区间），见 [依赖冲突讨论](https://discussions.unity.com/t/how-to-solve-conflicting-dependencies-from-two-different-packages/793647)。本仓库策略是：**与 `unity/ParrotDev` 同一解析路径** —— 不在 ArSpike 的 `manifest.json` 中声明 `xr.management`，锁文件中与 ParrotDev 对齐为 **4.4.0**（首次打开 Unity 后若 Unity 微调锁文件属正常）。

## 打开工程后

首次 `git pull` 后在本机用 Unity 打开 **ArSpike** 时，若 Package Manager 仍提示解析差异，点一次 **Resolve** / 等待重新解析即可；若遇异常缓存，可关闭 Unity 后删除 `Library` 再开（最后手段）。

## 相关文档

- 测试床 AR 版本与宏：`unity/ParrotDev`、`.cursor/rules/ar-foundation.mdc`
- 正式 App 流程 / UI 设计：`docs/sprint4_research/result/03_App_Flow_and_UI_Layout_Design.md`
- Sprint4 协议背景锚点：`.cursor/memory/architecture/sprint4_protocol_ecp_background_20260429.md`
- ECP 最小实现审计：`.cursor/memory/architecture/sprint4_ecp_minimal_audit_20260429.md`
- LiveKit Unity 视频管线 skill：`.cursor/skills/livekit-unity-video-publish/IMPL_REF.md`
- ParrotCarriers 模块索引：`.cursor/memory/INDEX.md`


