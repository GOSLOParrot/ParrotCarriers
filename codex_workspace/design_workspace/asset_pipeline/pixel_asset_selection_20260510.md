# Pixel Asset 整理结果 2026-05-10

> 来源：`D:\GOSLOParrot\Pixel Asset`  
> 工作区：`D:\GOSLOParrot\ParrotCarriers\codex_workspace\design_workspace\asset_pipeline\pixel_asset_workspace`

## 已处理素材包

| 素材包 | 原始数量印象 | 当前定位 |
|:--|:--|:--|
| `MagicalUI 1.1` | 63 PNG | 主 UI。书页、卷轴、标题条、纸面、魔法地图元素最统一。 |
| `Book UI V1` | 138 PNG | 书页、书签、面板、暗/亮色框补充。 |
| `Fantasy Book UI V2` | 160 PNG | 更装饰化的框、书页、图标，适合菜单画布节点。 |
| `Wood UI` | 10 PNG | 木制按钮/抽屉/标题补充，适合 START、工具抽屉。 |
| `Paper UI` | 7 PNG | 报纸/纸张，适合 Papers Please 式工作桌。 |
| `AdventureUI` | 53 PNG | 图标、按钮、背包/宝箱等次级装饰。 |
| `moderninteriors-win` | 7150 PNG | 只精选 186 PNG 作为 2D 宅邸/工作区白膜。 |
| `Craftland` | 57 PNG | 只精选 24 PNG 备用，不作为主风格。 |
| `Pixelwood Valley Icon Pack` / `RPGEMS` | 少量 | 低优先级杂项。 |

## Curated 目录分配

| 目录 | PNG 数量 | 说明 |
|:--|--:|:--|
| `curated/00_previews/` | 14 | 原包预览 + curated 分组预览。 |
| `curated/00_licenses/` | 0 PNG / 5 文本 | 授权、readme、第三方说明。 |
| `curated/01_primary_ui_magic/` | 63 | 第一版大 UI 主风格。 |
| `curated/02_ui_supplements_book_paper_wood/` | 315 | 书页、纸张、木制 UI 补充。 |
| `curated/03_secondary_ui_adventure/` | 53 | 次级按钮/图标/装饰。 |
| `curated/04_2d_workspace_modern_interiors/` | 186 | 2D 工作区、宅邸、书桌、室内 tilesheet。 |
| `curated/05_2d_workspace_craftland_backup/` | 24 | 备用 props。 |
| `curated/06_icons_and_misc/` | 2 | 杂项图标。 |

## 第一版白膜素材策略

1. **启动页**：主牌、`SCENE` 面板、Room Setting 展开页先用 `MagicalUI`；`START` 和底部按钮优先用 `Wood UI`。
2. **启动转场**：进度条和信息面板用 `MagicalUI` 的卷轴/纸面；飞行动画角色后续单独生成或自制。
3. **AR 主界面 HUD**：左上 HUD 先用 `MagicalUI` 暗化变体；右下工具抽屉用 `Wood UI` + `AdventureUI` 小图标。
4. **菜单画布**：Model / Persona / Mode / Scene / 2DWorkspace 节点先用 `MagicalUI` 和 `Fantasy Book UI V2`，保持“书页/魔法卷轴/模块卡”统一感。
5. **2D 工作区宅邸**：先用 `moderninteriors` 的 16x16 room builder 和 theme sheets 搭大厅、书桌、工作房间。
6. **工作桌/报告/纸条**：用 `Paper UI` + `Book UI V1`，专门承接 Obsidian / Google / PhotoNode 的纸面反馈和批改互动。

## 后续待做

- 按 Unity 实际 UI prefab 需要，给核心面板挑 9-slice 候选图并记录 slice 边界。
- 给 `2DModelPortrait`、鹦鹉桌宠、启动转场飞行动画单独建角色资产槽。
- 素材进入正式工程前再次检查授权文本，尤其是 `moderninteriors-win` 和 `Craftland`。
- 如果用户继续往 `D:\GOSLOParrot\Pixel Asset` 放 zip，新包只做临时解压；审图后只保留进入 `curated/` 的子集，并清理临时解压区。
