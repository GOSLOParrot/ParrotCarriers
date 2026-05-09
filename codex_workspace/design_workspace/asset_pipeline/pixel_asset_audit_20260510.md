# Pixel Asset 审计与第一版使用建议

> 来源：`D:\GOSLOParrot\Pixel Asset`  
> 状态：只登记候选，不移动大包进仓库。

## 1. 已发现素材

| 路径/包 | 大小/性质 | 建议用途 |
|:--|:--|:--|
| `Paper UI/BlankNewspaper_*.png` | 小图 | 报告纸条、Google draft、Obsidian note preview |
| `Paper UI/FilledNewspaper_*.png` | 小图 | Nanobot 已完成报告 |
| `Paper UI/Bro.....png` | 中等 | 报告桌装饰或测试纸张 |
| `AdventureUI.zip` | UI 包 | 按钮/面板候选 |
| `Book UI V1.zip` | UI 包 | Obsidian 设定书 |
| `Fantasy Book UI V2.zip` | UI 包 | RolePlay 设定书 |
| `MagicalUI 1.1.zip` | UI 包 | GOSLO Module / Awareness |
| `Pixelwood Valley Icon Pack 1.0.zip` | icon 包 | 外部模块图标 |
| `Wood UI.zip` | 小 UI 包 | 菜单画布木质按钮 |
| `Craftland.zip` | 大包 | 暂不解压，后续挑 2DWorkspace 场景素材 |
| `moderninteriors-win.zip` | 大包 | 暂不解压，后续挑室内背景 |

## 2. 第一版策略

- 先用白膜 UI + Paper UI 小图做 paper note / report desk。
- 大 zip 不直接入 Unity，避免资源爆炸。
- 每个模块先用一种图标或纸条形态占位。
- 等 App 流程稳定后，再把素材裁切、命名、导入 Unity `Assets/UI/`。

## 3. 模块映射

| App 模块 | 候选素材 |
|:--|:--|
| Google Calendar | Paper UI + simple calendar icon |
| Obsidian | Book UI / Fantasy Book UI |
| GOSLO Module | Magical UI |
| Nanobot | Filled Newspaper / report paper |
| Photo / Camera | Pixelwood icon |
| XRHand | Pixelwood hand/tool icon |
| Canvas Connection | Wood UI |
